import pyrr.matrix33
from pyrr import vector3, vector, Vector3, matrix44
from math import sin, cos, radians


# radians in case of angle being calculated from the proportion of window size traveled

class Camera:
    def __init__(self):
        # camera_pos starts 20 units away from target in z axis
        self.distance_to_target = 50.0
        self.camera_target = Vector3([0.0, 0.0, 0.0])

        self.camera_pos = self.camera_target + Vector3([0.0, 0.0, self.distance_to_target])
        self.camera_direction = vector.normalise(self.camera_pos - self.camera_target)
        self.camera_up = Vector3([0.0, 1.0, 0.0])
        self.camera_right = Vector3([1.0, 0.0, 0.0])

        self.angle_conversion_horizontal = 0.025
        self.angle_conversion_vertical = 0.0125

        self.alpha = 0
        self.beta = 0

    def get_view_matrix(self):
        # eye, target, up
        return matrix44.create_look_at(self.camera_pos, self.camera_direction, self.camera_up)

    # WIP WIP WIP WIP WIP
    def mouse_movement_rotate_item(self, x_offset, y_offset):
        self.alpha += -x_offset * self.angle_conversion_horizontal
        self.beta += -y_offset * self.angle_conversion_vertical

        # move_horizontal = Vector3([self.distance_to_target * sin(alpha), 0.0,
        # -self.distance_to_target * (1 - cos(alpha))])

        # move_vertical = Vector3([0.0, self.distance_to_target * cos(alpha) * sin(beta),
        # -self.distance_to_target * cos(alpha) * (1 - cos(beta))])

        # move_horizontal = Vector3([0.0, -self.distance_to_target * sin(beta),
        # -self.distance_to_target * (1 - cos(beta))])

        # move_vertical = Vector3([self.distance_to_target * cos(beta) * sin(alpha), 0.0,
        # -self.distance_to_target * cos(beta) * (1 - cos(alpha))])

        rot_around_y = pyrr.matrix33.create_from_y_rotation(self.alpha)
        rot_around_x = pyrr.matrix33.create_from_x_rotation(self.beta)

        # new_position = pyrr.matrix33.apply_to_vector(vec=self.camera_pos,
        # mat=pyrr.matrix33.multiply(rot_around_x, rot_around_y))

        # new_position = pyrr.matrix33.apply_to_vector(vec=self.camera_pos, mat=rot_around_y)
        # new_position = pyrr.matrix33.apply_to_vector(vec=new_position, mat=rot_around_x)

        return rot_around_x, rot_around_y

    def update_camera_position(self, new_position):
        self.camera_pos = new_position
        self.camera_direction = vector.normalise(self.camera_pos - self.camera_target)
        self.camera_right = vector.normalise(vector3.cross(self.camera_direction, Vector3([0.0, 1.0, 0.0])))
        self.camera_up = vector.normalise(vector3.cross(self.camera_right, self.camera_direction))

    def scroll(self, distance):
        self.update_camera_position(self.camera_pos + Vector3([0.0, 0.0, distance]))
