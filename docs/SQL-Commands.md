# Useful SQL Commands

Change type of column from varchar to boolean:
```
ALTER TABLE robot_logs ALTER bottom_validated TYPE boolean USING CASE bottom_validated WHEN 'true' THEN true ELSE NULL END;
```