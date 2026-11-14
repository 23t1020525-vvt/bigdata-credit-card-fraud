import os
import sys
import json
import glob
import hashlib
import io
import shutil
from datetime import datetime, timezone
from pyspark.sql import SparkSession

if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Thực hiện việc băm dữ liệu
def compute_file_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def check_existing_hash(manifest_dir, target_hash):
    """Kiểm tra xem mã SHA-256 của file nguồn đã tồn tại trong lịch sử Manifest chưa."""
    if not os.path.exists(manifest_dir):
        return None
    for m_file in sorted(glob.glob(os.path.join(manifest_dir, "manifest_run_*.json"))):
        try:
            with open(m_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # So sánh cả key cũ (sha256_hash) và key mới (source_sha256)
                past_hash = data.get("source_sha256") or data.get("sha256_hash")
                if data.get("status") == "SUCCESS" and past_hash == target_hash:
                    return data
        except Exception:
            continue
    return None


def run_ingestion(source_file_path):
    # 1. Quality Gate: Kiểm tra tồn tại và dung lượng > 0
    if not os.path.exists(source_file_path) or os.path.getsize(source_file_path) == 0:
        print(f"[ERROR] Khong tim thay file nguon hoac file rong tai: {source_file_path}")
        print("Vui long tai file creditcard.csv tu Kaggle va dat vao data/source_input/")
        sys.exit(1)

    manifest_dir = os.path.join("metadata", "manifests")
    os.makedirs(manifest_dir, exist_ok=True)

    # 2. Băm file nguồn
    source_hash = compute_file_hash(source_file_path)
    print(f"[INFO] SHA-256 file nguon: {source_hash}")

    # 3. Đối chiếu với lịch sử Manifest (Tránh tạo file mới nếu dữ liệu y hệt)
    matched_manifest = check_existing_hash(manifest_dir, source_hash)
    if matched_manifest:
        print("\n" + "=" * 55)
        print("[SKIP] Du lieu nguon TRUNG KHOP 100% voi lan nap truoc!")
        print(f"       -> Run da ton tai : {matched_manifest.get('run_id')}")
        print(f"       -> Vi tri file Raw: {matched_manifest.get('destination_path')}")
        print("[INFO] Khong tao them file moi de tranh trung lap du lieu.")
        print("=" * 55 + "\n")
        return

    now = datetime.now(timezone.utc)
    ingest_date = now.strftime("%Y-%m-%d")
    run_timestamp = now.strftime("%Y%m%d_%H%M%S")
    run_id = f"run_{run_timestamp}"

    print(f"[INGESTION] Dang nap du lieu tu nguon: {source_file_path}")

    raw_base_dir = "data/raw/credit_card_transactions"
    existing_raw_files = glob.glob(os.path.join(raw_base_dir, "**", "*.csv"), recursive=True)

    raw_dest_dir = f"{raw_base_dir}/ingest_date={ingest_date}/{run_id}"
    raw_output_file = os.path.join(raw_dest_dir, "raw_transactions.csv")

    # 4. Nếu chưa từng có file Raw nào -> Copy nguyên bản (Full Initial)
    if not existing_raw_files:
        os.makedirs(raw_dest_dir, exist_ok=True)
        shutil.copyfile(source_file_path, raw_output_file)
        with open(raw_output_file, "r", encoding="utf-8") as f:
            record_count = max(0, sum(1 for _ in f) - 1)
        ingest_mode = "FULL_INITIAL"

    # 5. Nếu đã có file Raw trước đó nhưng SHA-256 nguồn thay đổi -> Lọc phần còn thiếu (Delta)
    else:
        print("[INFO] Phat hien file nguon co cap nhat. Dang dung PySpark loc phan du lieu con thieu...")
        spark = SparkSession.builder.appName("CreditCard_Delta_Ingest").master("local[*]").getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")

        df_source = spark.read.option("header", "true").csv(source_file_path)
        df_existing = spark.read.option("header", "true").csv(existing_raw_files)

        # Lấy các dòng có trong source nhưng chưa có trong các file raw cũ
        df_delta = df_source.exceptAll(df_existing)
        record_count = df_delta.count()

        if record_count == 0:
            print("[SKIP] Khong co ban ghi moi nao can ghi them (0 delta rows). Huy tao file moi!")
            spark.stop()
            return

        os.makedirs(raw_dest_dir, exist_ok=True)
        df_delta.toPandas().to_csv(raw_output_file, index=False)
        ingest_mode = "INCREMENTAL_DELTA"
        spark.stop()

    file_bytes = os.path.getsize(raw_output_file)
    raw_file_hash = compute_file_hash(raw_output_file)

    manifest_data = {
        "dataset_name": "credit_card_transactions",
        "ingest_mode": ingest_mode,
        "ingest_timestamp_utc": now.isoformat(),
        "run_id": run_id,
        "source_path": source_file_path,
        "source_sha256": source_hash,
        "destination_path": raw_output_file.replace("\\", "/"),
        "record_count": record_count,
        "file_size_bytes": file_bytes,
        "sha256_hash": raw_file_hash,
        "status": "SUCCESS"
    }

    manifest_path = os.path.join(manifest_dir, f"manifest_{run_id}.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4)

    print("\n" + "=" * 50)
    print(f"[SUCCESS] Che do: {ingest_mode} | Da nap {record_count:,} ban ghi!")
    print(f"[RAW LOCATION] {raw_output_file}")
    print(f"[MANIFEST CREATED] {manifest_path}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    SOURCE_PATH = "data/source_input/creditcard.csv"
    run_ingestion(SOURCE_PATH)