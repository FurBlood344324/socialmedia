import io
from tests.base_test import BaseTest

class TestUploadController(BaseTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()

    def test_upload_file_no_file(self):
        resp = self.client.post('/api/upload/')
        assert resp.status_code == 400
        assert resp.get_json()['error'] == 'No file part'

    def test_upload_file_empty_filename(self):
        data = {'file': (io.BytesIO(b""), "")}
        resp = self.client.post('/api/upload/', data=data, content_type='multipart/form-data')
        assert resp.status_code == 400
        assert resp.get_json()['error'] == 'No selected file'

    def test_upload_file_invalid_extension(self):
        data = {'file': (io.BytesIO(b"test content"), "test.txt")}
        resp = self.client.post('/api/upload/', data=data, content_type='multipart/form-data')
        assert resp.status_code == 400
        assert resp.get_json()['error'] == 'File type not allowed'

    def test_upload_file_success(self):
        data = {'file': (io.BytesIO(b"image data"), "test.png")}
        resp = self.client.post('/api/upload/', data=data, content_type='multipart/form-data')
        assert resp.status_code == 201
        json_data = resp.get_json()
        assert 'url' in json_data
        assert json_data['url'].endswith('test.png')

    def test_generate_avatar_no_username(self):
        resp = self.client.post('/api/upload/generate-avatar', json={})
        assert resp.status_code == 400
        assert resp.get_json()['error'] == 'Username is required'

    def test_generate_avatar_user_not_found(self):
        resp = self.client.post('/api/upload/generate-avatar', json={"username": "nonexistent"})
        assert resp.status_code == 404
        assert resp.get_json()['error'] == 'User not found'

    def test_generate_avatar_success(self):
        # Create user first
        self.client.post('/api/auth/register', json={
            "username": "avatar_test",
            "email": "avatar@test.com",
            "password": "password"
        })
        
        resp = self.client.post('/api/upload/generate-avatar', json={"username": "avatar_test"})
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert 'url' in json_data
        assert 'message' in json_data
        assert json_data['message'] == 'Avatar generated successfully'
