#!/usr/bin/env python3
"""
Quick runner script - Chạy experiment trên dữ liệu có sẵn
"""

import os
import sys
import argparse
from pathlib import Path

# Fix lỗi Import: add cả thư mục cha ngoài cùng (để import được framework và solvers)
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from framework.experiment import ExperimentRunner
# Đưa utils lên đầu
from solvers.utils import read_cbus_file


def main():
    parser = argparse.ArgumentParser(
        description='CBUS Solver Comparison',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-d', '--data-dir', default=None,
                        help='Data directory path. Nếu không truyền sẽ tự tìm thư mục cbus_output* mới nhất')
    parser.add_argument('-t', '--time', type=float, default=None,
                        help='Time limit per solver in seconds (default: 30)')
    parser.add_argument('-i', '--instances', default=None,
                        help='Run specific instances (comma-separated, without .txt)')
    parser.add_argument('-o', '--output', default=None,
                        help='Output directory (default: auto-generated)')
    parser.add_argument('-q', '--quick', action='store_true',
                        help='Run quick test on first 3 instances')
    
    args = parser.parse_args()

    # 1. Logic tìm data_dir thông minh và an toàn hơn
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        # Tìm thư mục dạng cbus_output_* trong data/
        import glob
        data_parent = root_dir / 'data'
        possible_dirs = sorted(glob.glob(str(data_parent / 'cbus_output_*')))
        if possible_dirs:
            data_dir = Path(possible_dirs[-1]) # Lấy thư mục mới nhất
        else:
            data_dir = data_parent # Cực chẳng đã mới dùng fallback
            
    if not os.path.exists(data_dir):
        print(f"Error: Cannot find data directory at {data_dir}")
        sys.exit(1)

    # 2. Logic set time limit an toàn
    time_limit = args.time if args.time is not None else (10.0 if args.quick else 30.0)
    
    runner = ExperimentRunner(output_dir=args.output, time_limit=time_limit)
    
    # Hàm helper nội bộ thay vì lặp code
    def process_and_save(file_names):
        for f in file_names:
            file_path = os.path.join(data_dir, f)
            if not os.path.exists(file_path):
                print(f"⚠️  Instance not found: {f}")
                continue
            instance_name = f.replace('.txt', '')
            n, k, cost_matrix = read_cbus_file(file_path)
            
            # Ghi nhận kết quả
            result = runner.run_instance(instance_name, n, k, cost_matrix)
            runner.results['instances'][instance_name] = result
            
        runner._save_results() # Tạm chấp nhận gọi hàm internal nếu không tiện sửa ruột ExperimentRunner

    # 3. Phân luồng chạy
    if args.quick:
        print(f"\n🚀 Running quick test (3 instances, {time_limit}s per solver)...")
        files = sorted([f for f in os.listdir(data_dir) if f.endswith('.txt')])[:3]
        process_and_save(files)
        
    elif args.instances:
        instance_names = [name.strip() + '.txt' for name in args.instances.split(',')]
        print(f"\n🎯 Running {len(instance_names)} selected instance(s) ({time_limit}s per solver)...")
        process_and_save(instance_names)
        
    else:
        print(f"\n📊 Running all instances ({time_limit}s per solver)...")
        runner.run_all_instances(data_dir)


if __name__ == "__main__":
    main()