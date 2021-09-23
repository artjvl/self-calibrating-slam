//
// Created by art on 17-07-21.
//

#ifndef G2O_PARAMETER_SE2_H
#define G2O_PARAMETER_SE2_H

#include "node_se2.h"
#include "parameter.h"

namespace g2o {
    class ParameterSE2 : public NodeSE2, public Param {
    public:
        ParameterSE2();
        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;
        Vector3 toVector3() const override;
    };
}

#endif //G2O_PARAMETER_SE2_H
