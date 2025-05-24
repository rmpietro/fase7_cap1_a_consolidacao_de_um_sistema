from enum import Enum

class CropStreetAreaType(Enum):
    Rectangle = 1
    Triangle = 2

def crop_area_calculation(num_streets, crop_street_area_type, street_length, street_width):
    if crop_street_area_type == CropStreetAreaType.Rectangle:
        crop_area = num_streets * (street_length * street_width)
    elif crop_street_area_type == CropStreetAreaType.Triangle:
        crop_area = num_streets * (street_length * street_width) / 2
    else:
        raise print("Tipo de área de cultivo inválido. Escolha 'Retângulo' ou 'Triângulo'.")
    return crop_area

def sugar_cane_area_calculation(num_streets_s1, num_streets_s2, street_length_s1, street_length_s2, street_width):
    rectangle_area1 = crop_area_calculation(num_streets_s1, CropStreetAreaType.Rectangle, street_length_s1, street_width)
    rectangle_area2 = crop_area_calculation(num_streets_s2-1, CropStreetAreaType.Rectangle, street_length_s2, street_width)
    triangle_street_area = crop_area_calculation(1, CropStreetAreaType.Triangle, street_length_s2, street_width)
    return rectangle_area1 + rectangle_area2 + triangle_street_area

def corn_area_calculation(num_streets, street_length, street_width):
    rectangle_area = crop_area_calculation(num_streets, CropStreetAreaType.Rectangle, street_length, street_width)
    return rectangle_area