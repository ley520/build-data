# coding=utf-8
# data：2023/3/2-17:06
import jmespath
from rest_framework.exceptions import ValidationError
import jmespath
import re

# 匹配变量引用 ${0—>key1.key2[0]}
regex_compile = re.compile(r"\${[^}]+}")


def get_all_raw_string(content):
    """
    匹配出字符串中所有的变量引用
    Examples：
        content = "aabbcc${1->name.age}ddeefff${2->job.name}gg"
        解析结果：["${1->name.age}","${2->job.name}"]
    @param content:
    @return:
    """
    result_list = regex_compile.findall(content)
    return result_list


def parser_raw_variable(raw_variable):
    """
    解析变量引用
    Examples：
        raw_variable = ${1->job.name}
        解析后：[1,"job.name"]
    @param raw_variable:
    @return:
    """
    result: list = raw_variable[2:-1].split("->")
    if len(result) != 2:
        raise ValidationError(detail=f"变量引用解析失败：{raw_variable}")
    result[0] = int(result[0])
    return result


def replace_raw_string_with_variables(
    content: str, raw_variable_list: list, variables_mapping: dict
):
    """

    @param content:原始文本内容
    @param raw_variable_list:从content匹配到的所有变量引用
    @param variables_mapping:该任务的全局参数
    @return:
    """
    for raw_variable in raw_variable_list:
        parser_result = parser_raw_variable(raw_variable)
        variable_value = jmespath.search(
            parser_result[1], variables_mapping.get(parser_result[0])
        )
        content = content.replace(raw_variable, str(variable_value))
    return content


def replace_values(content, variables_mapping: dict):
    if isinstance(content, dict):
        for k, v in content.items():
            content[k] = replace_values(v, variables_mapping)
        return content
    elif isinstance(content, str):
        parser_raw_result: list = get_all_raw_string(content)
        return replace_raw_string_with_variables(
            content, parser_raw_result, variables_mapping
        )
    else:
        return content


if __name__ == "__main__":
    data = {
        "field1": "some string with ${1->name.job}",
        "field2": 123,
        "field3": {"nested_field": "another string with ${2->name.job}"},
        "field4": {
            "nested_field": {"deeply_nested_field": "string with ${3->name.job}"}
        },
    }

    result = replace_values(
        data,
        {
            1: {"name": {"job": "123"}},
            2: {"name": {"job": "456"}},
            3: {"name": {"job": "789"}},
        },
    )
    print(result)
