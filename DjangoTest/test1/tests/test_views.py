from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from test1.views import home_page
from test1.models import Item,List
from unittest import skip
from django.utils.html import escape
# Create your tests here.
class SmokeTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found=resolve('/')
        self.assertEqual(found.func,home_page)

    def test_home_page_returns_correct_html(self):
        request =HttpRequest()
        response =home_page(request)
        self.assertTrue(response.content.startswith(b'<html>'))
        self.assertIn(b'<title>To-Do Lists</title>',response.content)
        self.assertTrue(response.content.endswith(b'</html>'))
        
class ListViewTest(TestCase):
    def test_displays_only_items_for_that_list(self):
        correct_list=List.objects.create()
        Item.objects.create(text='itemey 1',list=correct_list)
        Item.objects.create(text='itemey 2',list=correct_list)
        
        other_list=List.objects.create()
        Item.objects.create(text='other list item 1',list=other_list)
        Item.objects.create(text='other list item 2',list=other_list)
        #TestCase自带的测试客户端self.client
        response=self.client.get('/lists/%d/'%(correct_list.id,))
        self.assertContains(response,'itemey 1')  
        self.assertContains(response,'itemey 2')   
        self.assertNotContains(response,'other list item 1')
        self.assertNotContains(response,'other list item 2')
    #检查是否使用list.html模板   
    def test_uses_list_template(self):
        list_=List.objects.create()
        response=self.client.get('/lists/%d/'%(list_.id,))
        self.assertTemplateUsed(response,'list.html')
        
    def test_passes_correct_list_to_template(self):
        other_list=List.objects.create()
        correct_list=List.objects.create()
        response=self.client.get('/lists/%d/'%(correct_list.id,))
        self.assertEqual(response.context['list'],correct_list)
        
class NewListTest(TestCase):
    
    def test_saving_a_POST_request(self):
        self.client.post(
        '/lists/new/',
        data={'item_text':'A new list item'}
        )
        self.assertEqual(Item.objects.count(),1)
        new_item=Item.objects.first()
        self.assertEqual(new_item.text,'A new list item')    
        
        
    def test_redirects_after_POST(self):
        response=self.client.post(
        '/lists/new/',
        data={'item_text':'A new list item'}
        )
        self.assertEqual(response.status_code,302)
        new_list=List.objects.first()
        self.assertRedirects(response,'/lists/%d/'%(new_list.id,))
    
    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response=self.client.post('/lists/new/',data={'item_text': ''})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home.html')
        expected_error= escape("You can't have an empty list item")
        self.assertContains(response,expected_error)
        
class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        otrher_list=List.objects.create()
        correct_list=List.objects.create()
        
        self.client.post(
            '/lists/%d/add_item'%(correct_list.id,),
            data={'item_text':'A new item for an existing list'}
        )
        
        self.assertEqual(Item.objects.count(),1)
        new_item=Item.objects.first()
        self.assertEqual(new_item.text,'A new item for an existing list')
        self.assertEqual(new_item.list,correct_list)
        
    def test_redirects_to_list_view(self):
        otrher_list=List.objects.create()
        correct_list=List.objects.create()
        
        response=self.client.post(
            '/lists/%d/add_item'%(correct_list.id,),
            data={'item_text':'A new item for an existing list'}
        )
        
        self.assertRedirects(response,'/lists/%d/'%(correct_list.id,))
        
    @skip
    def test_cannot_add_empty_list_items(self):
        self.fail('write me!')