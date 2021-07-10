//
// Created by art on 09-07-21.
//

#include "param_offset.h"

namespace g2o {

    ParamOffset::ParamOffset() : NodeSE2() {
    }

    SE2 ParamOffset::composeTransformation(const SE2 &transformation, const bool inverse) const {
        SE2 parameter = estimate();
        if (inverse) {
            parameter = parameter.inverse();
        }
        return parameter * transformation * parameter.inverse();
    }

}