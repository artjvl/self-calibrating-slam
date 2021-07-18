//
// Created by art on 18-07-21.
//

#ifndef G2O_CONSTRAINT_POSES2D_SE2_V3_H
#define G2O_CONSTRAINT_POSES2D_SE2_V3_H

#include "g2o/core/base_fixed_sized_edge.h"
#include "g2o/types/slam2d/se2.h"
#include "node_se2.h"
#include "parameter_v3.h"
#include "parameter_util.h"

namespace g2o {
    class ConstraintPoses2DSE2V3 : public BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParameterV3> {
    public:
        ConstraintPoses2DSE2V3();
        void computeError() {
            NodeSE2* n1 = static_cast<NodeSE2*>(_vertices[0]);
            NodeSE2* n2 = static_cast<NodeSE2*>(_vertices[1]);
            ParameterV3* p = static_cast<ParameterV3*>(_vertices[2]);

            const SE2& p1 = n1->estimate();
            const SE2& p2 = n2->estimate();
            std::string interpretation = p->interpretation();

            SE2 delta = p1.inverse() * p2;
            SE2 error = _inverseMeasurement * ParameterUtil::transform(interpretation, delta, p->toVector3(), true);
            _error = error.toVector();
        }
        void setMeasurement(const SE2& m){
            _measurement = m;
            _inverseMeasurement = m.inverse();
        }
        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;

    protected:
        SE2 _inverseMeasurement;
    };
}

#endif //G2O_CONSTRAINT_POSES2D_SE2_V3_H
