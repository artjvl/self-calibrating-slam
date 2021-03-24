//
// Created by art on 23-03-21.
//

#ifndef G2O_PARAM_V2_H
#define G2O_PARAM_V2_H

#include "node_v2.h"
#include "param.h"

namespace g2o {
    class ParamV2 : public NodeV2, public Param {
    public:
        EIGEN_MAKE_ALIGNED_OPERATOR_NEW
        ParamV2();

        bool setType(const std::string &type) override;
    };
}

#endif //G2O_PARAM_V2_H
