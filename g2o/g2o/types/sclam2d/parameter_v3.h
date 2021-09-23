//
// Created by art on 17-07-21.
//

#ifndef G2O_PARAMETER_V3_H
#define G2O_PARAMETER_V3_H

#include "node_v3.h"
#include "parameter.h"

namespace g2o {
    class ParameterV3 : public NodeV3, public Param {
    public:
        ParameterV3();
        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;
        Vector3 toVector3() const override;
    };
}

#endif //G2O_PARAMETER_V3_H
