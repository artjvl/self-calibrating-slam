//
// Created by art on 23-03-21.
//

#include "constraint_poses2d_se2_pse2.h"

namespace g2o {
    ConstraintPoses2DSE2PSE2::ConstraintPoses2DSE2PSE2() :
        BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamSE2>() {
    }

    bool ConstraintPoses2DSE2PSE2::read(std::istream& is) {

        // read measurement
        Vector3 p;
        internal::readVector(is, p);
        setMeasurement(SE2(p));

        // read parameter-type
        ParamSE2* node_param = getParamSE2();
        std::string param_type;
        is >> param_type;
        node_param->setType(param_type);

        // read information matrix
        readInformationMatrix(is);

        return is.good() || is.eof();
    }

    bool ConstraintPoses2DSE2PSE2::write(std::ostream &os) const {

        // write measurement
        internal::writeVector(os, measurement().toVector());

        // write parameter_type
        const ParamSE2 *node_param = getParamSE2();
        os << node_param->getType() << " ";

        // write information matrix
        return writeInformationMatrix(os);
    }
}