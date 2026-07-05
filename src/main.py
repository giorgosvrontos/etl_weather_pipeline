from extract import extract_marine_data
from transform import transform_marine_data
from load import load_data_to_postgres

def run_etl_pipeline():
    print("ETL pipeline starting...")

    raw_data = extract_marine_data()
    
    if not raw_data:
        print("❌ The Extract step failed. The pipeline stops.")
        return

    final_marine_data = transform_marine_data(raw_data)

    load_data_to_postgres(final_marine_data)

    print("🎉 The ETL Pipeline completed successfully!")

# This tells Python to run the function when we execute the file
if __name__ == "__main__":
    run_etl_pipeline()