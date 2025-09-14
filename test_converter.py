# test_numeric_converter.py

import pytest
import json
import base64
from api.index import app, text_to_number, number_to_text, base64_to_number, number_to_base64


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestUtilityFunctions:
    """Test the individual utility functions."""
    
    def test_text_to_number_basic(self):
        """Test basic text to number conversions."""
        assert text_to_number('one') == 1
        assert text_to_number('five') == 5
        assert text_to_number('ten') == 10
        assert text_to_number('zero') == 0
        assert text_to_number('nil') == 0
        assert text_to_number('forty two') == 42
    
    def test_text_to_number_case_insensitive(self):
        """Test text to number with different cases."""
        assert text_to_number('ONE') == 1
        assert text_to_number('Five') == 5
        assert text_to_number('TEN') == 10
    
    def test_text_to_number_with_punctuation(self):
        """Test text to number with punctuation removal."""
        assert text_to_number('one!') == 1
        assert text_to_number('five,') == 5
        assert text_to_number('ten.') == 10
    
    def test_text_to_number_invalid(self):
        """Test text to number with invalid input."""
        with pytest.raises(ValueError):
            text_to_number('eleven')
        with pytest.raises(ValueError):
            text_to_number('invalid')
        with pytest.raises(ValueError):
            text_to_number('')
    
    def test_number_to_text_basic(self):
        """Test basic number to text conversions."""
        assert number_to_text(1) == 'one'
        assert number_to_text(0) == 'zero'
        assert number_to_text(42) == 'forty-two'
        assert number_to_text(100) == 'one hundred'
    
    def test_number_to_text_large_numbers(self):
        """Test number to text with larger numbers."""
        assert number_to_text(1000) == 'one thousand'
        assert number_to_text(1234) == 'one thousand, two hundred and thirty-four'
    
    def test_base64_conversions(self):
        """Test base64 encoding/decoding functions."""
        # Test small numbers
        assert base64_to_number(number_to_base64(1)) == 1
        assert base64_to_number(number_to_base64(42)) == 42
        assert base64_to_number(number_to_base64(255)) == 255
        
        # Test larger numbers
        assert base64_to_number(number_to_base64(1000)) == 1000
        assert base64_to_number(number_to_base64(65535)) == 65535
    
    def test_base64_to_number_invalid(self):
        """Test base64 to number with invalid input."""
        with pytest.raises(ValueError):
            base64_to_number('invalid_base64!')
        with pytest.raises(ValueError):
            base64_to_number('')
    
    def test_number_to_base64_edge_cases(self):
        """Test number to base64 with edge cases."""
        # Test zero
        result = number_to_base64(0)
        assert base64_to_number(result) == 0
        
        # Test power of 2
        result = number_to_base64(256)
        assert base64_to_number(result) == 256


class TestFlaskRoutes:
    """Test the Flask application routes."""
    
    def test_index_route(self, client):
        """Test the index route returns successfully."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_convert_route_method_not_allowed(self, client):
        """Test convert route only accepts POST requests."""
        response = client.get('/convert')
        assert response.status_code == 405


class TestConversions:
    """Test all conversion combinations through the API endpoint."""
    
    def make_conversion_request(self, client, input_value, input_type, output_type):
        """Helper method to make conversion requests."""
        return client.post('/convert',
                          json={
                              'input': input_value,
                              'inputType': input_type,
                              'outputType': output_type
                          },
                          content_type='application/json')
    
    # Test conversions from decimal
    def test_decimal_to_all_formats(self, client):
        """Test conversions from decimal to all other formats."""
        test_cases = [
            ('42', 'decimal', 'text', 'forty-two'),
            ('42', 'decimal', 'binary', '101010'),
            ('42', 'decimal', 'octal', '52'),
            ('42', 'decimal', 'decimal', '42'),
            ('42', 'decimal', 'hexadecimal', '2a'),
        ]
        
        for input_val, input_type, output_type, expected in test_cases:
            response = self.make_conversion_request(client, input_val, input_type, output_type)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['error'] is None
            assert data['result'] == expected
        
        # Test base64 separately since it's harder to predict exact output
        response = self.make_conversion_request(client, '42', 'decimal', 'base64')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['error'] is None
        # Verify we can convert back
        back_response = self.make_conversion_request(client, data['result'], 'base64', 'decimal')
        back_data = json.loads(back_response.data)
        assert back_data['result'] == '42'
    
    # Test conversions from binary
    def test_binary_to_all_formats(self, client):
        """Test conversions from binary to all other formats."""
        test_cases = [
            ('101010', 'binary', 'text', 'forty-two'),
            ('101010', 'binary', 'binary', '101010'),
            ('101010', 'binary', 'octal', '52'),
            ('101010', 'binary', 'decimal', '42'),
            ('101010', 'binary', 'hexadecimal', '2a'),
        ]
        
        for input_val, input_type, output_type, expected in test_cases:
            response = self.make_conversion_request(client, input_val, input_type, output_type)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['error'] is None
            assert data['result'] == expected
    
    # Test conversions from octal
    def test_octal_to_all_formats(self, client):
        """Test conversions from octal to all other formats."""
        test_cases = [
            ('52', 'octal', 'text', 'forty-two'),
            ('52', 'octal', 'binary', '101010'),
            ('52', 'octal', 'octal', '52'),
            ('52', 'octal', 'decimal', '42'),
            ('52', 'octal', 'hexadecimal', '2a'),
        ]
        
        for input_val, input_type, output_type, expected in test_cases:
            response = self.make_conversion_request(client, input_val, input_type, output_type)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['error'] is None
            assert data['result'] == expected
    
    # Test conversions from hexadecimal
    def test_hexadecimal_to_all_formats(self, client):
        """Test conversions from hexadecimal to all other formats."""
        test_cases = [
            ('2a', 'hexadecimal', 'text', 'forty-two'),
            ('2a', 'hexadecimal', 'binary', '101010'),
            ('2a', 'hexadecimal', 'octal', '52'),
            ('2a', 'hexadecimal', 'decimal', '42'),
            ('2a', 'hexadecimal', 'hexadecimal', '2a'),
        ]
        
        for input_val, input_type, output_type, expected in test_cases:
            response = self.make_conversion_request(client, input_val, input_type, output_type)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['error'] is None
            assert data['result'] == expected
    
    # Test conversions from text
    def test_text_to_all_formats(self, client):
        """Test conversions from text to all other formats."""
        test_cases = [
            ('five', 'text', 'text', 'five'),
            ('five', 'text', 'binary', '101'),
            ('five', 'text', 'octal', '5'),
            ('five', 'text', 'decimal', '5'),
            ('five', 'text', 'hexadecimal', '5'),
        ]
        
        for input_val, input_type, output_type, expected in test_cases:
            response = self.make_conversion_request(client, input_val, input_type, output_type)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['error'] is None
            assert data['result'] == expected
    
    # Test conversions from base64
    def test_base64_to_all_formats(self, client):
        """Test conversions from base64 to all other formats."""
        # First, get a base64 representation of 42
        response = self.make_conversion_request(client, '42', 'decimal', 'base64')
        base64_value = json.loads(response.data)['result']
        
        test_cases = [
            (base64_value, 'base64', 'text', 'forty-two'),
            (base64_value, 'base64', 'binary', '101010'),
            (base64_value, 'base64', 'octal', '52'),
            (base64_value, 'base64', 'decimal', '42'),
            (base64_value, 'base64', 'hexadecimal', '2a'),
            (base64_value, 'base64', 'base64', base64_value),
        ]
        
        for input_val, input_type, output_type, expected in test_cases:
            response = self.make_conversion_request(client, input_val, input_type, output_type)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['error'] is None
            assert data['result'] == expected


class TestEdgeCases:
    """Test edge cases and special values."""
    
    def make_conversion_request(self, client, input_value, input_type, output_type):
        """Helper method to make conversion requests."""
        return client.post('/convert',
                          json={
                              'input': input_value,
                              'inputType': input_type,
                              'outputType': output_type
                          },
                          content_type='application/json')
    
    def test_zero_conversions(self, client):
        """Test conversions involving zero."""
        test_cases = [
            ('0', 'decimal', 'text', 'zero'),
            ('0', 'decimal', 'binary', '0'),
            ('0', 'decimal', 'octal', '0'),
            ('0', 'decimal', 'hexadecimal', '0'),
            ('zero', 'text', 'decimal', '0'),
            ('nil', 'text', 'decimal', '0'),
        ]
        
        for input_val, input_type, output_type, expected in test_cases:
            response = self.make_conversion_request(client, input_val, input_type, output_type)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['error'] is None
            assert data['result'] == expected
    
    def test_large_numbers(self, client):
        """Test conversions with large numbers."""
        large_num = '1000000'
        response = self.make_conversion_request(client, large_num, 'decimal', 'text')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['error'] is None
        assert 'million' in data['result']
    
    def test_case_insensitive_hex(self, client):
        """Test hexadecimal input is case insensitive."""
        test_cases = [
            ('ff', 'hexadecimal', 'decimal', '255'),
            ('FF', 'hexadecimal', 'decimal', '255'),
            ('Ff', 'hexadecimal', 'decimal', '255'),
        ]
        
        for input_val, input_type, output_type, expected in test_cases:
            response = self.make_conversion_request(client, input_val, input_type, output_type)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['error'] is None
            assert data['result'] == expected


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def make_conversion_request(self, client, input_value, input_type, output_type):
        """Helper method to make conversion requests."""
        return client.post('/convert',
                          json={
                              'input': input_value,
                              'inputType': input_type,
                              'outputType': output_type
                          },
                          content_type='application/json')
    
    def test_invalid_input_types(self, client):
        """Test invalid input type parameter."""
        response = self.make_conversion_request(client, '42', 'invalid', 'decimal')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
        assert 'Invalid input type' in data['error']
    
    def test_invalid_output_types(self, client):
        """Test invalid output type parameter."""
        response = self.make_conversion_request(client, '42', 'decimal', 'invalid')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
        assert 'Invalid output type' in data['error']
    
    def test_invalid_binary_input(self, client):
        """Test invalid binary input."""
        response = self.make_conversion_request(client, '123', 'binary', 'decimal')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
    
    def test_invalid_octal_input(self, client):
        """Test invalid octal input."""
        response = self.make_conversion_request(client, '89', 'octal', 'decimal')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
    
    def test_invalid_hex_input(self, client):
        """Test invalid hexadecimal input."""
        response = self.make_conversion_request(client, 'xyz', 'hexadecimal', 'decimal')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
    
    def test_invalid_text_input(self, client):
        """Test invalid text input."""
        response = self.make_conversion_request(client, 'eleven', 'text', 'decimal')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
    
    def test_invalid_base64_input(self, client):
        """Test invalid base64 input."""
        response = self.make_conversion_request(client, 'invalid_base64!', 'base64', 'decimal')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
    
    def test_empty_input(self, client):
        """Test empty input values."""
        response = self.make_conversion_request(client, '', 'decimal', 'text')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None
        
    def test_missing_parameters(self, client):
        """Test missing required parameters."""
        response = client.post('/convert',
                              json={'input': '42'},
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] is None
        assert data['error'] is not None


if __name__ == '__main__':
    pytest.main([__file__])