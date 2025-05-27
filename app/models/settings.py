from app import db

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    type = db.Column(db.String(20))  # string, int, bool, json
    
    def __repr__(self):
        return f'<Setting {self.key}>'
    
    @staticmethod
    def get(key, default=None):
        setting = Settings.query.filter_by(key=key).first()
        if not setting:
            return default
            
        if setting.type == 'int':
            return int(setting.value)
        elif setting.type == 'bool':
            return setting.value.lower() == 'true'
        elif setting.type == 'json':
            import json
            return json.loads(setting.value)
        return setting.value
    
    @staticmethod
    def set(key, value, type='string'):
        setting = Settings.query.filter_by(key=key).first()
        if not setting:
            setting = Settings(key=key)
            
        if type == 'json':
            import json
            setting.value = json.dumps(value)
        else:
            setting.value = str(value)
            
        setting.type = type
        db.session.add(setting)
        db.session.commit()
        
    @staticmethod
    def get_all():
        """Return all settings as a dictionary"""
        settings = {}
        for setting in Settings.query.all():
            if setting.type == 'int':
                settings[setting.key] = int(setting.value)
            elif setting.type == 'bool':
                settings[setting.key] = setting.value.lower() == 'true'
            elif setting.type == 'json':
                import json
                settings[setting.key] = json.loads(setting.value)
            else:
                settings[setting.key] = setting.value
        return settings 