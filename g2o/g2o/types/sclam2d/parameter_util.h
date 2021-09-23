//
// Created by art on 17-07-21.
//

#ifndef G2O_PARAMETER_UTIL_H
#define G2O_PARAMETER_UTIL_H

#include <g2o/core/eigen_types.h>
#include "g2o/types/slam2d/se2.h"

namespace g2o {
    class ParameterUtil {
    public:
        static SE2 transform_bias(const SE2& transformation, const Vector3& vector, bool is_inverse) {
            Vector3 v = vector;
            if (is_inverse) v = - v;
            return transformation * SE2(v);
        }
        static SE2 transform_offset(const SE2& transformation, const Vector3& vector, bool is_inverse) {
            Vector3 v = vector;
            if (is_inverse) v = - v;
            SE2 offset = SE2(v);
            return offset * transformation * offset.inverse();
        }
        static SE2 transform_scale(const SE2& transformation, const Vector3& vector, bool is_inverse) {
            Vector3 v = vector;
            if (is_inverse) {
                for (int i = 0; i < 3; i++) v[i] = 1 / v[i];
            }
            return SE2(v.asDiagonal() * transformation.toVector());
        }
        static SE2 transform(const std::string& interpretation, SE2& transformation, const Vector3& vector) {
            return transform(interpretation, transformation, vector, false);
        }
        static SE2 transform(const std::string& interpretation, const SE2& transformation, const Vector3& vector, bool is_inverse) {
            assert (interpretation == "bias" || interpretation == "offset" || interpretation == "scale");
            if (interpretation == "bias") {
                return transform_bias(transformation, vector, is_inverse);
            } else if (interpretation == "offset") {
                return transform_offset(transformation, vector, is_inverse);
            } else if (interpretation == "scale") {
                return transform_scale(transformation, vector, is_inverse);
            } else {
                return transformation;
            }
        }
        static Vector2 translate(const std::string& interpretation, const Vector2& translation, const Vector3& vector, bool is_inverse) {
            SE2 pose = SE2(translation[0], translation[1], 0.0);
            return transform(interpretation, pose, vector, is_inverse).translation();
        }
        static Vector2 translate(const std::string& interpretation, const Vector2& translation, const Vector3& vector) {
            return translate(interpretation, translation, vector, false);
        }
    };
}

#endif //G2O_PARAMETER_UTIL_H
