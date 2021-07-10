//
// Created by art on 09-07-21.
//

#include "constraint_poses2d_se2_scale.h"

namespace g2o {

    ConstraintPoses2DSE2Scale::ConstraintPoses2DSE2Scale() :
            BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamScale>() {
    }

    bool ConstraintPoses2DSE2Scale::read(std::istream& is) {
        Vector3 p;
        internal::readVector(is, p);
        _measurement.fromVector(p);
        _inverseMeasurement=measurement().inverse();
        return readInformationMatrix(is);
    }

    bool ConstraintPoses2DSE2Scale::write(std::ostream& os) const {
        internal::writeVector(os, measurement().toVector());
        return writeInformationMatrix(os);
    }

} // end namespace