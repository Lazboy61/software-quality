class ScooterManager:
    def __init__(self, conn):
        self.conn = conn

    def validate_gps(self, lat, lon):
        # Rotterdam gebied coördinaten
        return (51.85 <= lat <= 52.00) and (4.30 <= lon <= 4.55)
    
    def validate_location(lat, lon):
        return (51.85 <= lat <= 52.00) and (4.30 <= lon <= 4.55)

    def update_scooter(self, scooter_id, updates, role):
        allowed_fields = {
            'superadmin': ['all'],
            'sysadmin': ['all'],
            'engineer': ['soc', 'mileage', 'out_of_service']
        }.get(role, [])

        if 'all' not in allowed_fields:
            updates = {k: v for k, v in updates.items() if k in allowed_fields}

        cursor = self.conn.cursor()
        # Update query uitvoeren
        self.conn.commit()