import os


class Crypt():        

    __private_key_path='jwt-private.pem'
    __public_key_path='jwt-public.pem'
    __private_key = None
    __public_key = None

    @staticmethod
    def get_private_key():
        '''
        Возвращает приватный RSA ключ.
        '''
        if Crypt.__private_key is None:
            Crypt.__private_key, Crypt.__public_key = Crypt.load_keys()
        return Crypt.__private_key

    @staticmethod
    def get_public_key():
        '''
        Возвращает публичный RSA ключ.
        '''
        if Crypt.__public_key is None:
            Crypt.__private_key, Crypt.__public_key = Crypt.load_keys()
        return Crypt.__public_key

    @staticmethod
    def load_keys():
        '''
        Returns private_key, public_key 
        '''
        
        if not os.path.exists(Crypt.__private_key_path):
            Crypt.__generate_rsa_keys()
        
        try:    
            with open(Crypt.__private_key_path, 'rb') as f:
                private_key = f.read()
            with open(Crypt.__public_key_path, 'rb') as f:
                public_key = f.read()
            return private_key, public_key
        except Exception as _:
            exit()

    @staticmethod
    def __generate_rsa_keys():
        """
        Генерирует приватный и публичный RSA ключи.
        """

        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization

        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()
        except Exception as e:
            print(f"Error generating keys: {e}")
            exit()
        
        try:
            with open(Crypt.__private_key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            with open(Crypt.__public_key_path, 'wb') as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo 
                ))
        except Exception as _:
            exit()
