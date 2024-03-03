
def write_file(number):
    #content = request.get_json()  # Get the request body as JSON
    with open('data.txt', 'w') as f:
       # f.write(content['data'])
         f.write(number)
    return 'Success', 200


def read_file():
    with open('data.txt', 'r') as f:
        content = f.read()
    return content
