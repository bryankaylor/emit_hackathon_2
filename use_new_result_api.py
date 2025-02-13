import json
import time

from result_manager import Radio, Band, Combination, ResultManager


def main():
    project = r'C:\Program Files\ANSYS Inc\v251\AnsysEM\Examples\EMIT\AH-64 Apache Cosite.aedt'
    result_manager = ResultManager(project)
    result_manager.print_radio_data()
    combo_count = result_manager.count_combos()

    print(f'Simulating {combo_count} combinations ...')
    start_time = time.time()
    results = result_manager.get_combos()
    end_time = time.time()
    total_time = end_time - start_time
    print(f'Done simulating {combo_count} combinations in {total_time}s.')

    json_result = json.dumps(results, default=lambda x: x.__dict__, indent='  ')
    with open('combos.json', 'w') as file:
        file.write(json_result)


if __name__ == '__main__':
    main()
