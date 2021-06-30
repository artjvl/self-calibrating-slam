//
// Created by art on 24-04-21.
//

#ifndef G2O_CONSTRAINT_POSES2D_SE2_PV3_H
#define G2O_CONSTRAINT_POSES2D_SE2_PV3_H

#include "g2o/core/base_fixed_sized_edge.h"
#include "g2o/types/slam2d/se2.h"
#include "node_se2.h"
#include "param_v3.h"

namespace g2o {

    class ConstraintPoses2DSE2PV3 : public BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamV3> {
    public:
        ConstraintPoses2DSE2PV3();

        void computeError() {
            const NodeSE2* v1   = static_cast<const NodeSE2*>(_vertices[0]);
            const NodeSE2* v2   = static_cast<const NodeSE2*>(_vertices[1]);
            const ParamV3* p    = static_cast<const ParamV3*>(_vertices[2]);

            const SE2& x1 = v1->estimate();
            const SE2& x2 = v2->estimate();
            const std::string interpretation = p->getInterpretation();
            const Vector3& par = p->estimate();

            SE2 delta = x1.inverse() * x2;
            SE2 error;

            // decomposition: estimate = delta - parameters
            if (interpretation == "SCALE") {
                Eigen::Matrix<double, 3, 3> diagonal = par.asDiagonal();
                Vector3 scaled = diagonal.inverse() * delta.toVector();
                error = _inverseMeasurement * SE2(scaled);
            } else {
                error = _inverseMeasurement * delta;
            }
            _error = error.toVector();
        }

        void setMeasurement(const SE2& m){
            _measurement = m;
            _inverseMeasurement = m.inverse();
        }

        virtual number_t initialEstimatePossible(const OptimizableGraph::VertexSet& from, OptimizableGraph::Vertex* to) {
            if (from.count(_vertices[2]) == 1 // need the laser offset
                   && ((from.count(_vertices[0]) == 1 && to == _vertices[1]) || ((from.count(_vertices[1]) == 1 && to == _vertices[0])))) {
                return 1.0;
            }
            return -1.0;
        }

        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;

    protected:
        SE2 _inverseMeasurement;
    };

} // end namespace

#endif //G2O_CONSTRAINT_POSES2D_SE2_PV3_H
