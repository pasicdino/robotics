import numpy as np

class KalmanFilter:
    def __init__(self, initial_state, initial_covariance, process_noise, measurement_noise, robot):
        self.state = np.array(initial_state)
        self.covariance = np.array(initial_covariance)
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.robot = robot  # Store the robot object


    def predict(self, control_input, dt):
        # Unpack state
        x, y, theta = self.state
        v, omega = control_input

        # Motion model
        dx = v * np.cos(theta) * dt
        dy = v * np.sin(theta) * dt
        dtheta = omega * dt

        # Predicted state
        x += dx
        y += dy
        theta += dtheta

        # Normalize orientation
        theta = (theta + np.pi) % (2 * np.pi) - np.pi

        self.state = [x, y, theta]

        # Jacobian of the motion model
        F = np.array([[1, 0, -dy],
                      [0, 1, dx],
                      [0, 0, 1]])

        # Update covariance
        self.covariance = F @ self.covariance @ F.T + self.process_noise

    def update(self, measurements):
        # measurements is a list of (distance, bearing, feature_id)
        for distance, bearing, feature_id in measurements:
            # Expected measurement based on current state and map feature location
            feature_x, feature_y = self.robot.map.features[feature_id]
            expected_distance, expected_bearing = self.calculate_expected_measurement(feature_x, feature_y)

            def update(self, measurements):
                for distance, bearing, feature_id in measurements:
                    try:
                        feature_x, feature_y = self.robot.map.features[feature_id]
                        # Continue with processing
                    except KeyError:
                        print(f"No feature found for ID: {feature_id}")
                        continue  # Skip this measurement
            # Measurement residual
            z_res = np.array([distance - expected_distance, bearing - expected_bearing])

            # Measurement matrix
            H = np.array([[1, 0, 0], [0, 1, 0]])

            # Residual covariance
            S = H @ self.covariance @ H.T + self.measurement_noise

            # Kalman gain
            K = self.covariance @ H.T @ np.linalg.inv(S)

            # Update state
            self.state += K @ z_res

            # Update covariance
            self.covariance = (np.eye(3) - K @ H) @ self.covariance

    def calculate_expected_measurement(self, feature_x, feature_y):
        # Calculate expected distance and bearing based on current state
        x, y, theta = self.state
        dx = feature_x - x
        dy = feature_y - y
        distance = np.sqrt(dx**2 + dy**2)
        bearing = np.atan2(dy, dx) - theta
        return distance, bearing


def update(self, measurements):
    try:
        for distance, bearing, feature_id in measurements:
            # Process each measurement
            # Update state and covariance based on the Kalman Filter equations
            pass
    except TypeError as e:
        print(f"Error in measurement format: {e}")
