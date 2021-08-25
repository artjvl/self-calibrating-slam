//
// Created by art on 17-07-21.
//

#ifndef G2O_NODE_V1_H
#define G2O_NODE_V1_H

#include "g2o/core/base_vertex.h"

namespace g2o {
    class NodeV1 : public BaseVertex<1, number_t> {
    public:
        NodeV1();
        virtual void setToOriginImpl() {
            _estimate = 0.0;
        }
        virtual bool setEstimateDataImpl(const number_t* est) {
            _estimate = *est;
            return true;
        }
        virtual bool getEstimateData(number_t* est) const {
            *est = _estimate;
            return true;
        }
        virtual int estimateDimension() const {
            return 1;
        }
        virtual bool setMinimalEstimateDataImpl(const number_t* est) {
            return setEstimateData(est);
        }
        virtual bool getMinimalEstimateData(number_t* est) const {
            return getEstimateData(est);
        }
        virtual int minimalEstimateDimension() const {
            return 1;
        }
        virtual void oplusImpl(const number_t* update) {
            _estimate += *update;
        }
        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;
    };
}

#endif //G2O_NODE_V1_H
