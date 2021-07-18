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
        static SE2 transform_bias(const SE2& transformation, const Vector3& parameter) {
            return transformation * SE2(parameter);
        }
        static SE2 transform_offset(const SE2& transformation, const Vector3& parameter) {
            SE2 offset = SE2(parameter);
            return offset * transformation * offset.inverse();
        }
        static SE2 transform_scale(const SE2& transformation, const Vector3& parameter) {
            return SE2(parameter.asDiagonal() * transformation.toVector());
        }
        static SE2 transform(const std::string& interpretation, SE2& transformation, const Vector3& parameter) {
            return transform(interpretation, transformation, parameter, false);
        }
        static SE2 transform(const std::string& interpretation, const SE2& transformation, const Vector3& parameter, bool inverse) {
            assert (interpretation == "bias" || interpretation == "offset" || interpretation == "scale");
            Vector3 par = parameter;
            if (inverse) {
                par = - par;
            }
            if (interpretation == "bias") {
                return transform_bias(transformation, par);
            } else if (interpretation == "offset") {
                return transform_offset(transformation, par);
            } else if (interpretation == "scale") {
                return transform_scale(transformation, par);
            } else {
                return transformation;
            }
        }
        static Vector2 translate(const std::string& interpretation, const Vector2& translation, const Vector3& parameter, bool inverse) {
            SE2 pose = SE2(translation[0], translation[1], 0.0);
            return transform(interpretation, pose, parameter, inverse).translation();
        }
        static Vector2 translate(const std::string& interpretation, const Vector2& translation, const Vector3& parameter) {
            return translate(interpretation, translation, parameter, false);
        }
    };
}

#endif //G2O_PARAMETER_UTIL_H
