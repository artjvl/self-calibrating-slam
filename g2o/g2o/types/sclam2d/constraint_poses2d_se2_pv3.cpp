//
// Created by art on 24-04-21.
//

#include "constraint_poses2d_se2_pv3.h"

namespace g2o {

    ConstraintPoses2DSE2PV3::ConstraintPoses2DSE2PV3() :
            BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamV3>()
    {
    }

    bool ConstraintPoses2DSE2PV3::read(std::istream& is) {
        Vector3 p;
        internal::readVector(is, p);
        _measurement.fromVector(p);
        _inverseMeasurement=measurement().inverse();
        return readInformationMatrix(is);
    }

    bool ConstraintPoses2DSE2PV3::write(std::ostream& os) const {
        internal::writeVector(os, measurement().toVector());
        return writeInformationMatrix(os);
    }

} // end namespace
