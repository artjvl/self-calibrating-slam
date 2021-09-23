//
// Created by art on 17-07-21.
//

#ifndef G2O_PARAMETER_V1_H
#define G2O_PARAMETER_V1_H

#include "node_v1.h"
#include "parameter.h"

namespace g2o {
    class ParameterV1 : public NodeV1, public Param {
    public:
        ParameterV1();
        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;
        Vector3 toVector3() const override;
    protected:
        int _index;
    };
}

#endif //G2O_PARAMETER_V1_H
