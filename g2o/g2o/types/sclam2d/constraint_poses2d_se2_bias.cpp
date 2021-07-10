//
// Created by art on 09-07-21.
//

#include "constraint_poses2d_se2_bias.h"

namespace g2o {

    ConstraintPoses2DSE2Bias::ConstraintPoses2DSE2Bias() :
            BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamBias>()
    {
    }

    void ConstraintPoses2DSE2Bias::initialEstimate(const OptimizableGraph::VertexSet& from, OptimizableGraph::Vertex* to) {
        (void) to;
        NodeSE2* vi = static_cast<NodeSE2*>(_vertices[0]);
        NodeSE2* vj = static_cast<NodeSE2*>(_vertices[1]);
        ParamBias* l = static_cast<ParamBias*>(_vertices[2]);
        if (from.count(l) == 0)
            return;
        if (from.count(vi) == 1) {
            vj->setEstimate(vi->estimate() * l->estimate() * measurement() * l->estimate().inverse());
        } else {
            vi->setEstimate(vj->estimate() * l->estimate() * _inverseMeasurement * l->estimate().inverse());
        }
    }

    bool ConstraintPoses2DSE2Bias::read(std::istream& is) {
        Vector3 p;
        internal::readVector(is, p);
        _measurement.fromVector(p);
        _inverseMeasurement=measurement().inverse();
        return readInformationMatrix(is);
    }

    bool ConstraintPoses2DSE2Bias::write(std::ostream& os) const {
        internal::writeVector(os, measurement().toVector());
        return writeInformationMatrix(os);
    }

} // end namespace