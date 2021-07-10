//
// Created by art on 09-07-21.
//

#ifndef G2O_PARAM_SCALE_H
#define G2O_PARAM_SCALE_H

#include "node_v3.h"
#include "param.h"

namespace g2o {
    class ParamScale : public NodeV3, public Param {
    public:
        ParamScale();
        SE2 composeTransformation(const SE2& transformation, const bool inverse) const;
    };
}

#endif //G2O_PARAM_SCALE_H
