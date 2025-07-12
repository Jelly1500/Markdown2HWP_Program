"""
XML 처리 유틸리티 함수 모듈
"""
from bs4 import BeautifulSoup
import re

def create_soup(xml_content=None, features='xml'):
    """BeautifulSoup 객체 생성"""
    if xml_content:
        return BeautifulSoup(xml_content, features)
    return BeautifulSoup(features=features)

def find_elements(soup, selector, recursive=True):
    """XML에서 요소 찾기"""
    return soup.find_all(selector, recursive=recursive)

def find_first_element(soup, selector):
    """XML에서 첫 번째 일치 요소 찾기"""
    return soup.find(selector)

def get_attribute(element, attribute, default=None):
    """요소의 속성값 가져오기"""
    return element.get(attribute, default)

def set_attribute(element, attribute, value):
    """요소의 속성 설정"""
    element[attribute] = value
    return element

def replace_section_content(xml_content, pattern, replacement, flags=re.DOTALL):
    """정규식 패턴에 따라 XML 내용의 일부를 교체"""
    return re.sub(pattern, lambda m: replacement, xml_content, flags=flags)

def create_new_element(soup, tag_name, attributes=None):
    """새 XML 요소 생성"""
    new_tag = soup.new_tag(tag_name)
    if attributes:
        for attr, value in attributes.items():
            new_tag[attr] = value
    return new_tag

def append_child(parent, child):
    """부모 요소에 자식 요소 추가"""
    parent.append(child)
    return parent 