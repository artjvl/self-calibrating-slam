//
// Created by art on 23-03-21.
//

#ifndef G2O_PARAM_SE2_H
#define G2O_PARAM_SE2_H

#include "node_se2.h"
#include "param.h"

namespace g2o {
    class ParamSE2 : public NodeSE2, public Param {
    public:
        EIGEN_MAKE_ALIGNED_OPERATOR_NEW
        ParamSE2();

        bool setType(const std::string &type) override;
    };
}

#endif //G2O_PARAM_SE2_H
