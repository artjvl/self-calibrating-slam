//
// Created by art on 15-06-21.
//

#include "constraint_info3.h"

namespace g2o {

    ConstraintInfo3::ConstraintInfo3() :
            BaseFixedSizedEdge<3, Vector3, Info3>(), _multiplier(0)
    {
    }

    bool ConstraintInfo3::read(std::istream& is) {
        is >> _multiplier;
        return internal::readVector(is, _measurement);
    }

    bool ConstraintInfo3::write(std::ostream& os) const {
        os << _multiplier << " ";
        return internal::writeVector(os, _measurement);
    }

}
