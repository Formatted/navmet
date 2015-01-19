

import itertools

import numpy as np
from .angle_utils import normalize


def edist(v1, v2):
    """
    Euclidean distance between the two [abs,ord] vectors v1 and v2

    Parameters
    -----------
    v1,v2 : float array
            two [abs, ord] points
    Returns
    -----------
    distance between v1 and v2
    """
    return np.sqrt((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2)


def point_dist(x1, y1, x2, y2, x3, y3):
    # x3,y3 is the point
    px = x2-x1
    py = y2-y1

    something = px*px + py*py

    u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    dist = np.sqrt(dx*dx + dy*dy)

    return dist


def normalize_vector((x1, y1), (x2, y2)):
    v = np.array([x1-x2, y1-y2])
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v/norm


def normalize_vector2(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v/norm


def vec_angle(p1, p2, p3, p4):
    nv1 = normalize_vector((p1[0], p1[1]), (p2[0], p2[1]))
    nv2 = normalize_vector((p3[0], p3[1]), (p4[0], p4[1]))
    angle = np.arccos(np.dot(nv1, nv2))
    return angle


def rotate2d(theta, px, py, ox, oy, direction='counter_clockwise'):
    if direction == 'counter_clockwise':
        ppx = (np.cos(theta) * (px-ox) - np.sin(theta) * (py-oy)) + ox
        ppy = (np.sin(theta) * (px-ox) + np.cos(theta) * (py-oy)) + oy
        return np.array([ppx, ppy])
    else:
        ppx = (np.cos(theta) * (px-ox) + np.sin(theta) * (py-oy)) + ox
        ppy = (-np.sin(theta) * (px-ox) + np.cos(theta) * (py-oy)) + oy
        return np.array([ppx, ppy])


def angle_horizontal(p1, p2):
    dx = p2[0]-p1[0]
    if dx > 0.0:
        rel_theta = normalize(vec_angle(p1, p2, (p1[0], p1[1]), (p1[0]+1, p1[1])))
    else:
        rel_theta = normalize(vec_angle(p1, p2, (p1[0], p1[1]), (p1[0]-1, p1[1])))
    return rel_theta


def eval_gaussian(x, mu, sigma=0.2):
    """
    Evaluate a Gaussian at a point
    """
    fg = (1.0 / sigma * np.sqrt(2*np.pi)) * np.exp(-(x - mu) / (2.0 * sigma))
    return fg / 100.0


def action_disturbance(action, relation, sigma=0.2, discount=0.99):
    """
    Compute the social relation disturbance for a single action,
    defined as crossing social links and computed by evaluating
    a Gaussian centered perpendicularly on the social link
    """
    a1, a2 = relation[0], relation[1]
    dy, dx = a2[1]-a1[1], a2[0]-a1[0]
    direction = 'counter_clockwise'
    if (dx > 0.0 and dy > 0.0) or (dx < 0.0 and dy < 0.0):
        direction = 'clockwise'

    # Rotate the relation to be parallel to the horizontal axis
    theta = angle_horizontal(a1, a2)
    ox, oy = a1[0], a1[1]  # rotate about a1

    a1r = rotate2d(theta, a1[0], a1[1], ox, oy, direction)
    a2r = rotate2d(theta, a2[0], a2[1], ox, oy, direction)

    # Rotate the action as well to match the new position of the social relation
    pts = list()
    for p in action:
        pts.append(rotate2d(theta, p[0], p[1], ox, oy, direction))

    # check the resulting action which are within the danger zone
    danger_actions = list()
    for i, j in itertools.izip(pts, pts[1:]):
        # check the y coordinates
        if (i[1] <= (a1r[1] + sigma) and i[1] >= (a1r[1] - sigma)) or (j[1] <= (a1r[1] + sigma) and j[1] >= (a1r[1] - sigma)):
            # check x coordinates
            if a1r[0] < a2r[0]:
                if (i[0] >= a1r[0] and i[0] <= a2r[0]) or (j[0] >= a1r[0] and j[0] <= a2r[0]):
                    current_action = (i, j)
                    danger_actions.append(current_action)
            elif a1r[0] > a2r[0]:
                if (i[0] <= a1r[0] and i[0] >= a2r[0]) or (j[0] <= a1r[0] and j[0] >= a2r[0]):
                    current_action = (i, j)
                    danger_actions.append(current_action)

    # Now process the dangerous action and compute the feature on them (evaluate the gaussian)
    feature = 0.0
    for i, da in enumerate(danger_actions):
        # find the distance to the line (for use in gaussian evaluation)
        stride = point_dist(a1r[0], a1r[1], a2r[0], a2r[1], da[1][0], da[1][1])
        feature += eval_gaussian(stride, mu=0.0, sigma=sigma) * discount**i

    return feature
