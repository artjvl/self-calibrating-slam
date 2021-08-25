//
// Created by art on 17-07-21.
//

#include "node_v1.h"

namespace g2o {
    NodeV1::NodeV1() : BaseVertex<1, number_t>() {
        _estimate = 0.0;
    }
    bool NodeV1::read(std::istream& is) {
        is >> _estimate;
        return is.good() || is.eof();
    }
    bool NodeV1::write(std::ostream& os) const {
        os << _estimate << " ";
        return os.good();
    }
}