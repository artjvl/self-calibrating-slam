//
// Created by art on 09-07-21.
//

#include "param_bias.h"

namespace g2o {

    ParamBias::ParamBias() : NodeSE2() {
    }

    SE2 ParamBias::composeTransformation(const SE2 &transformation, const bool inverse) const {
        SE2 parameter = estimate();
        if (inverse) {
            parameter = parameter.inverse();
        }
        return transformation * parameter;
    }

}