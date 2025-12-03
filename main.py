# diarization cli interface
import os
import sys
import yaml
from pipline.diarization import perform_diarization, save_diarization_result

def load_config():
    with open("config.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not file_path:
        print("Usage: python main.py <path-to-mp3>")
        sys.exit(1)

    base = os.path.splitext(file_path)[0]    
    # 1. Выполняем диаризацию
    diarization_result = perform_diarization(file_path, config)
    
    # 1.1 Сохраняем результат диаризации
    save_diarization_result(diarization_result, f"{base}.dia")

    print("✅ Готово!")

if __name__ == "__main__":
    main()
