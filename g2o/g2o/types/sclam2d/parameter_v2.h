//
// Created by art on 17-07-21.
//

#ifndef G2O_PARAMETER_V2_H
#define G2O_PARAMETER_V2_H

#include "node_v2.h"
#include "parameter.h"

namespace g2o {
    class ParameterV2 : public NodeV2, public Param {
    public:
        ParameterV2();
        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;
        Vector3 toVector3() const override;

    protected:
        int _index;
    };
}

#endif //G2O_PARAMETER_V2_H
