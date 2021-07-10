//
// Created by art on 09-07-21.
//

#include "param_scale.h"

namespace g2o {

    ParamScale::ParamScale() : NodeV3() {
    }

    SE2 ParamScale::composeTransformation(const SE2& transformation, const bool inverse) const {
        Vector3 parameter = estimate();
        if (inverse) {
            parameter = - parameter;
        }
        return SE2(parameter.asDiagonal() * transformation.toVector());
    }

}