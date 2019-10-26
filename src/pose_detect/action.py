import math

# from numba import jit


def raisehand(arr, id):
    if (
        arr[id, 4, 1] < arr[id, 3, 1]
        and arr[id, 4, 1] < arr[id, 2, 1]
        and arr[id, 4, 1] != 0
    ):
        return True
    elif (
        arr[id, 7, 1] < arr[id, 6, 1]
        and arr[id, 7, 1] < arr[id, 5, 1]
        and arr[id, 7, 1] != 0
    ):
        return True
    else:
        return False


def squat(arr, id, maxY, minY):
    total_long = maxY - minY
    long = 2.3 * (arr[id, 8, 1] - arr[id, 1, 1])
    if (
        (arr[id, 8, 1] > arr[id, 10, 1])
        and (arr[id, 9, 1] > arr[id, 10, 1])
        and (arr[id, 12, 1] > arr[id, 13, 1])
        and (arr[id, 10, 1] != 0)
        and (arr[id, 13, 1] != 0)
        and (total_long < long)
    ):
        return True
    elif (
        (arr[id, 8, 1] > arr[id, 13, 1])
        and (arr[id, 9, 1] > arr[id, 10, 1])
        and (arr[id, 12, 1] > arr[id, 13, 1])
        and (arr[id, 10, 1] != 0)
        and (arr[id, 13, 1] != 0)
        and (total_long < long)
    ):
        return True
    else:
        return False


def squat2(arr, id):
    now_Height = math.sqrt(
        math.pow(arr[id, 17, 0] - arr[id, 11, 0], 2)
        + math.pow(arr[id, 17, 1] - arr[id, 11, 1], 2)
    )
    R_Height = 0
    L_Height = 0
    if (
        arr[id, 17, 0] != 0
        and arr[id, 11, 0] != 0
        and arr[id, 17, 1] != 0
        and arr[id, 11, 1] != 0
        and arr[id, 2, 0] != 0
        and arr[id, 9, 0] != 0
        and arr[id, 2, 1] != 0
        and arr[id, 9, 1] != 0
        and arr[id, 10, 0] != 0
        and arr[id, 10, 1] != 0
    ):
        R_len_head = math.sqrt(
            math.pow(arr[id, 17, 0] - arr[id, 2, 0], 2)
            + math.pow(arr[id, 17, 1] - arr[id, 2, 1], 2)
        )
        R_Height = (
            R_len_head
            + math.sqrt(
                math.pow(arr[id, 2, 0] - arr[id, 9, 0], 2)
                + math.pow(arr[id, 2, 1] - arr[id, 9, 1], 2)
            )
            + math.sqrt(
                math.pow(arr[id, 9, 0] - arr[id, 10, 0], 2)
                + math.pow(arr[id, 9, 1] - arr[id, 10, 1], 2)
            )
            + math.sqrt(
                math.pow(arr[id, 10, 0] - arr[id, 11, 0], 2)
                + math.pow(arr[id, 10, 1] - arr[id, 11, 1], 2)
            )
        )
    if (
        arr[id, 18, 0] != 0
        and arr[id, 14, 0] != 0
        and arr[id, 18, 1] != 0
        and arr[id, 14, 1] != 0
        and arr[id, 5, 0] != 0
        and arr[id, 12, 0] != 0
        and arr[id, 5, 1] != 0
        and arr[id, 12, 1] != 0
        and arr[id, 13, 0] != 0
        and arr[id, 13, 1] != 0
    ):
        L_len_head = math.sqrt(
            math.pow(arr[id, 18, 0] - arr[id, 5, 0], 2)
            + math.pow(arr[id, 18, 1] - arr[id, 5, 1], 2)
        )
        L_Height = (
            L_len_head
            + math.sqrt(
                math.pow(arr[id, 5, 0] - arr[id, 12, 0], 2)
                + math.pow(arr[id, 5, 1] - arr[id, 12, 1], 2)
            )
            + math.sqrt(
                math.pow(arr[id, 12, 0] - arr[id, 13, 0], 2)
                + math.pow(arr[id, 12, 1] - arr[id, 13, 1], 2)
            )
            + math.sqrt(
                math.pow(arr[id, 13, 0] - arr[id, 14, 0], 2)
                + math.pow(arr[id, 13, 1] - arr[id, 14, 1], 2)
            )
        )
    if now_Height >= R_Height * 0.5 and now_Height <= R_Height * 3 / 4:
        return True
    elif now_Height >= L_Height * 0.5 and now_Height <= L_Height * 3 / 4:
        return True
    else:
        return False


def sit3(arr, id):
    now_Height = math.sqrt(
        math.pow(arr[id, 17, 0] - arr[id, 11, 0], 2)
        + math.pow(arr[id, 17, 1] - arr[id, 11, 1], 2)
    )
    R_Height = 0
    L_Height = 0
    if (
        arr[id, 17, 0] != 0
        and arr[id, 11, 0] != 0
        and arr[id, 17, 1] != 0
        and arr[id, 11, 1] != 0
        and arr[id, 2, 0] != 0
        and arr[id, 9, 0] != 0
        and arr[id, 2, 1] != 0
        and arr[id, 9, 1] != 0
        and arr[id, 10, 0] != 0
        and arr[id, 10, 1] != 0
    ):
        R_len_head = math.sqrt(
            math.pow(arr[id, 17, 0] - arr[id, 2, 0], 2)
            + math.pow(arr[id, 17, 1] - arr[id, 2, 1], 2)
        )
        R_Height = (
            R_len_head
            + math.sqrt(
                math.pow(arr[id, 2, 0] - arr[id, 9, 0], 2)
                + math.pow(arr[id, 2, 1] - arr[id, 9, 1], 2)
            )
            + math.sqrt(
                math.pow(arr[id, 9, 0] - arr[id, 10, 0], 2)
                + math.pow(arr[id, 9, 1] - arr[id, 10, 1], 2)
            )
            + math.sqrt(
                math.pow(arr[id, 10, 0] - arr[id, 11, 0], 2)
                + math.pow(arr[id, 10, 1] - arr[id, 11, 1], 2)
            )
        )
    if (
        arr[id, 18, 0] != 0
        and arr[id, 14, 0] != 0
        and arr[id, 18, 1] != 0
        and arr[id, 14, 1] != 0
        and arr[id, 5, 0] != 0
        and arr[id, 12, 0] != 0
        and arr[id, 5, 1] != 0
        and arr[id, 12, 1] != 0
        and arr[id, 13, 0] != 0
        and arr[id, 13, 1] != 0
    ):
        L_len_head = math.sqrt(
            math.pow(arr[id, 18, 0] - arr[id, 5, 0], 2)
            + math.pow(arr[id, 18, 1] - arr[id, 5, 1], 2)
        )
        L_Height = (
            L_len_head
            + math.sqrt(
                math.pow(arr[id, 5, 0] - arr[id, 12, 0], 2)
                + math.pow(arr[id, 5, 1] - arr[id, 12, 1], 2)
            )
            + math.sqrt(
                math.pow(arr[id, 12, 0] - arr[id, 13, 0], 2)
                + math.pow(arr[id, 12, 1] - arr[id, 13, 1], 2)
            )
            + math.sqrt(
                math.pow(arr[id, 13, 0] - arr[id, 14, 0], 2)
                + math.pow(arr[id, 13, 1] - arr[id, 14, 1], 2)
            )
        )
    if now_Height >= R_Height * 0.7 and now_Height <= R_Height * 0.88:
        return True
    elif now_Height >= L_Height * 0.7 and now_Height <= L_Height * 0.88:
        return True
    else:
        return False


def sitCalf(arr, id, maxY, minY):
    height = maxY - minY
    if arr[id, 10, 0] > 0 and arr[id, 11, 0] > 0:
        calf1 = math.sqrt(
            math.pow(arr[id, 10, 0] - arr[id, 11, 0], 2)
            + math.pow(arr[id, 10, 1] - arr[id, 11, 1], 2)
        )
    else:
        calf1 = 0

    if arr[id, 13, 0] > 0 and arr[id, 14, 0] > 0:
        calf2 = math.sqrt(
            math.pow(arr[id, 13, 0] - arr[id, 14, 0], 2)
            + math.pow(arr[id, 13, 1] - arr[id, 14, 1], 2)
        )
    else:
        calf2 = 0

    if calf1 == 0 and calf2 == 0:
        return False
    elif calf1 < calf2:
        calf1 = calf2

    max = calf1 * 3.4
    min = calf1 * 2.75
    if (height < max) and (height > min):
        return True
    else:
        return False


def benddown(arr, id):
    right_cos_C = 0
    left_cos_C = 0
    right_a = math.pow(arr[id, 2, 0] - arr[id, 9, 0], 2) + math.pow(
        arr[id, 2, 1] - arr[id, 9, 1], 2
    )
    right_b = math.pow(arr[id, 9, 0] - arr[id, 2, 0], 2) + math.pow(
        arr[id, 9, 1] - arr[id, 9, 1], 2
    )
    right_c = math.pow(arr[id, 2, 0] - arr[id, 2, 0], 2) + math.pow(
        arr[id, 2, 1] - arr[id, 9, 1], 2
    )
    left_a = math.pow(arr[id, 5, 0] - arr[id, 12, 0], 2) + math.pow(
        arr[id, 5, 1] - arr[id, 12, 1], 2
    )
    left_b = math.pow(arr[id, 12, 0] - arr[id, 5, 0], 2) + math.pow(
        arr[id, 12, 1] - arr[id, 12, 1], 2
    )
    left_c = math.pow(arr[id, 5, 0] - arr[id, 5, 0], 2) + math.pow(
        arr[id, 5, 1] - arr[id, 12, 1], 2
    )
    if right_a != 0 and right_b != 0:
        right_cos_C = (right_a + right_b - right_c) / math.sqrt(4 * right_a * right_b)
    if left_a != 0 and left_b != 0:
        left_cos_C = (left_a + left_b - left_c) / math.sqrt(4 * left_a * left_b)
    if right_cos_C > 0.34:
        return True
    elif left_cos_C > 0.34:
        return True
    else:
        return False


def sit2(arr, id):
    hipHeight = abs(arr[id, 11, 1] - arr[id, 9, 1])
    tmp = abs(arr[id, 14, 1] - arr[id, 12, 1])
    if tmp > hipHeight:
        hipHeight = tmp

    kneeHeight = abs(arr[id, 11, 1] - arr[id, 10, 1])
    tmp = abs(arr[id, 14, 1] - arr[id, 13, 1])
    if tmp > hipHeight:
        hipHeight = tmp

    differ = abs(hipHeight - kneeHeight)
    if differ < hipHeight * 0.25 or differ < kneeHeight * 0.25:
        return True
    else:
        return False


def kneel(arr, id):
    rhipToAnkle = -1
    lhipToAnkle = -1
    body = -1
    if arr[id, 11, 1] != 0 and arr[id, 10, 1] != 0:
        rhipToAnkle = abs(arr[id, 11, 1] - arr[id, 10, 1])
    if arr[id, 14, 1] != 0 and arr[id, 13, 1] != 0:
        lhipToAnkle = abs(arr[id, 14, 1] - arr[id, 13, 1])
    if arr[id, 1, 1] != 0 and arr[id, 8, 1] != 0:
        body = math.sqrt(
            math.pow(arr[id, 8, 0] - arr[id, 1, 0], 2)
            + math.pow(arr[id, 8, 1] - arr[id, 1, 1], 2)
        )

    if rhipToAnkle >= 0 and body * 0.3 > rhipToAnkle:
        return True
    elif lhipToAnkle >= 0 and body * 0.3 > lhipToAnkle:
        return True
    else:
        return False

