import numpy as np

class KalmanFilter:
    def __init__(self, initial_state, initial_covariance, process_noise, measurement_noise, robot, map):
        self.state = np.array(initial_state)  # State should typically include [x, y, orientation]
        self.covariance = np.array(initial_covariance)  # Initial covariance matrix
        self.process_noise = process_noise  # Process noise covariance matrix
        self.measurement_noise = measurement_noise  # Measurement noise covariance matrix
        self.path = [(self.state[0], self.state[1])]
        self.robot = robot  # Reference to the robot object, assuming it holds map information
        self.map = map

    def predict(self, control_input, dt):
        x, y, theta = self.state
        v, omega = control_input

        # Predict new state based on the robot's control inputs
        dx = v * np.cos(theta) * dt
        dy = v * np.sin(theta) * dt
        dtheta = omega * dt

        # Update state
        x += dx
        y += dy
        theta = (theta + dtheta) % (2 * np.pi)  # Normalize orientation

        self.state = np.array([x, y, theta])

        # Update covariance with the new Jacobian of the motion model
        F = np.array([[1, 0, -dy], [0, 1, dx], [0, 0, 1]])
        self.covariance = F @ self.covariance @ F.T + self.process_noise

    def update(self, measurements):
        for distance, bearing, feature_id in measurements:
            # Check if the feature ID is in the map features to handle measurements correctly
            if feature_id in self.map.features:
                feature_x, feature_y = self.robot.map.features[feature_id]
                expected_distance, expected_bearing = self.calculate_expected_measurement(feature_x, feature_y)
                z_res = np.array([distance - expected_distance, bearing - expected_bearing])

                # Measurement matrix
                H = np.array([[1, 0, 0], [0, 1, 0]])

                # Compute the residual covariance
                S = H @ self.covariance @ H.T + self.measurement_noise

                # Calculate Kalman gain
                K = self.covariance @ H.T @ np.linalg.inv(S)

                # Update the state with the new measurement
                self.state += K @ z_res

                # Update the covariance
                self.covariance = (np.eye(len(self.state)) - K @ H) @ self.covariance


        self.path.append((self.state[0], self.state[1]))


    def calculate_expected_measurement(self, feature_x, feature_y):
        # Calculate expected measurement based on the current state
        x, y, theta = self.state
        dx = feature_x - x
        dy = feature_y - y
        distance = np.sqrt(dx**2 + dy**2)
        bearing = np.arctan2(dy, dx) - theta

        return distance, bearing
