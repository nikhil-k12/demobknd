from helperlibrary.helper_module import Helper

aws_access_key = "AKIA4YY3D4A42BD3MGEK"
aws_secret_key = "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"
aws_region = "ap-south-1"

# Create an instance of the Helper class
helper_instance = Helper(aws_access_key,aws_secret_key,aws_region)

helper_instance.create_table('xyz')

# helper_instance.product_add_new_entry('xyz','test1','test prod1','test desc','abc')
attributes = {'name': 'Product Name', 'description': 'Product Description', 'imageurl': 'image_url'}
# helper_instance.add_new_entry('xyz','testy',attributes)


# allproducts = helper_instance.fetch_all_records('xyz')
# print(allproducts)

# res = helper_instance.fetch_records_by_field('xyz','id','test1')

# attributes_to_update = {'attribute1': 'c', 'attribute2': 'c','name': 'myn'}
# helper_instance.update_many_fields('xyz', 'test1', attributes_to_update)


# print(res)
# helper_instance.delete_record('xyz','test1')
# print(helper_instance.fetch_all_records('xyz'))

q_url = helper_instance.sqs_create_queue('test_q')
helper_instance.sqs_send_message_to_queue(q_url,'{"test":"test"}')

