//
// Created by art on 09-07-21.
//

#ifndef G2O_PARAM_OFFSET_H
#define G2O_PARAM_OFFSET_H

#include "node_se2.h"
#include "param.h"

namespace g2o {
    class ParamOffset : public NodeSE2, public Param {
    public:
        ParamOffset();
        SE2 composeTransformation(const SE2& transformation, const bool inverse) const;

    };
}

#endif //G2O_PARAM_OFFSET_H