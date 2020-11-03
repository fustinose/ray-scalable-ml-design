import argparse
import numpy as np

import pytorch_benchmarks
import ray

parser = argparse.ArgumentParser(description="PyTorch microbenchmarks")
parser.add_argument('test_name', type=str, default='auto',
                    help='Name of the test (multicast, reduce, allreduce, gather, allgather)')
parser.add_argument('-n', '--world-size', type=int, required=False,
                    help='Size of the collective processing group')
parser.add_argument('-s', '--object-size', type=int, required=False,
                    help='The size of the object')
args = parser.parse_args()


def test_with_mean_std(repeat_times, test_name, world_size, object_size):
    results = []
    for _ in range(repeat_times):
        test_case = pytorch_benchmarks.__dict__[test_name]
        duration = test_case(world_size, object_size)
        results.append(duration)
    return np.mean(results), np.std(results)


if __name__ == "__main__":
    ray.init(address='auto')
    test_name = 'pytorch_' + args.test_name
    assert test_name in pytorch_benchmarks.__dict__ or args.test_name == 'auto'
    if args.test_name != 'auto':
        assert args.world_size is not None and args.object_size is not None
        mean, std = test_with_mean_std(5, test_name, args.world_size, args.object_size)
        print(f"{args.test_name},{args.world_size},{args.object_size},{mean},{std}")
    else:
        assert args.world_size is None and args.object_size is None
        with open("pytorch-microbenchmark.csv", "w") as f:
            for algorithm in ('pytorch_broadcast', 'pytorch_gather', 'pytorch_reduce', 'pytorch_allreduce',
                              'pytorch_allgather'):
                for world_size in (4, 8, 12, 16):
                    for object_size in (2 ** 10, 2 ** 15, 2 ** 20, 2 ** 25, 2 ** 30):
                        mean, std = test_with_mean_std(5, algorithm, world_size, object_size)
                        print(f"{algorithm}, {world_size}, {object_size}, {mean}, {std}")
                        f.write(f"{algorithm},{world_size},{object_size},{mean},{std}\n")
