from lfocr import ocr
import json
import os


def test_json_output():

    afkar_input_file_path = f'{os.path.dirname(os.path.abspath(__file__))}/afkar_test.pdf'
    afkar_reference_file_path = f'{os.path.dirname(os.path.abspath(__file__))}/afkar_output_reference.json'
    temp = ocr()
    afkar_json_result = temp.process(afkar_input_file_path, 'afkar')
    
    with open(afkar_reference_file_path, 'r') as afkar_reference_file:
        afkar_json_reference = json.load(afkar_reference_file)

    # with open('afkar_text_output.json', 'w') as output:
    #     json.dump(afkar_json_result, output, ensure_ascii=False)

    assert afkar_json_reference == afkar_json_result


    # emtiaz_input_file_path = f'{os.path.dirname(os.path.abspath(__file__))}/emtiaz_test.pdf'
    # emtiaz_reference_file_path = f'{os.path.dirname(os.path.abspath(__file__))}/emtiaz_output_reference.json'
    # temp = ocr()
    # emtiaz_json_result = temp.process(emtiaz_input_file_path, 'emtiaz')
    # with open(emtiaz_reference_file_path, 'r') as emtiaz_reference_file:
    #     emtiaz_json_reference = json.load(emtiaz_reference_file)

    # assert emtiaz_json_reference == emtiaz_json_result


    # besharat_input_file_path = f'{os.path.dirname(os.path.abspath(__file__))}/besharat_test.pdf'
    # besharat_reference_file_path = f'{os.path.dirname(os.path.abspath(__file__))}/besharat_output_reference.json'
    # temp = ocr()
    # besharat_json_result = temp.process(besharat_input_file_path, 'besharat')
    # with open(besharat_reference_file_path, 'r') as besharat_reference_file:
    #     besharat_json_reference = json.load(besharat_reference_file)

    # assert besharat_json_reference == besharat_json_result
