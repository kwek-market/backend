import requests
import json


def get_post_office_data():
    # url = "https://services3.arcgis.com/BU6Aadhn6tbBEdyk/arcgis/rest/services/GRID3_NGA_Post_Offices/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
    # payload, headers={},{}
    # response = requests.request("GET", url, headers=headers, data=payload)
    # res_content = json.loads(response.content)
    # return res_content["features"]
    pass

class PostOffices():
    def __init__(self):
        self.offices_data = get_post_office_data()

    def get_all(self):
        return self.offices_data

    def get_for_state(self, state:str):
        post_os = []
        for i in self.offices_data: 
            post_os.append(i) if i["attributes"]["state_name"].lower() == state.lower() else False
                 
        return post_os

    def get_for_lga(self, lga:str):
        post_os = []
        for i in self.offices_data: 
            post_os.append(i) if i["attributes"]["lga_name"].lower() == lga.lower() else False
        return post_os

    def get_for_state_and_lga(self, state:str, lga:str):
        post_os = []
        for i in self.offices_data: 
            post_os.append(i) if (i["attributes"]["lga_name"].lower() == lga.lower()) and  (i["attributes"]["state_name"].lower() == state.lower()) else False
        return post_os


post_offices = PostOffices()


from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# First we create a little helper function, becase we will potentially have many PaginatedTypes 
# and we will potentially want to turn many querysets into paginated results:

def get_paginator(qs, page_size, page, paginated_type, **kwargs):
    p = Paginator(qs, page_size)
    try:
        page_obj = p.page(page)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    return paginated_type(
        page=page_obj.number,
        pages=p.num_pages,
        has_next=page_obj.has_next(),
        has_prev=page_obj.has_previous(),
        objects=page_obj.object_list,
        **kwargs
    )