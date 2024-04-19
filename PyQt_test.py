from database import DatabaseManager


test_dict = {
    'book_name': 'test',
    'book_path': 'test',
    'add_time': 'test',
}
db = DatabaseManager()
db.add_book(**test_dict)
