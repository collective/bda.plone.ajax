from Products.Five import BrowserView
from bda.plone.ajax.batch import Batch


RESULTLEN = 45
SLICESIZE = 10


class ExampleBatch(Batch):
    batchname = 'examplebatch'

    @property
    def vocab(self):
        ret = list()
        # len result
        count = RESULTLEN
        # entries per page
        slicesize = SLICESIZE
        # number of batch pages
        pages = count / slicesize
        if count % slicesize != 0:
            pages += 1
        # current batch page
        current = self.request.get('b_page', '0')
        for i in range(pages):
            # create query with page number
            query = 'b_page=%s' % str(i)
            # create batch target url
            url = '%s?%s' % (self.context.absolute_url(), query)
            # append batch page
            ret.append({
                'page': '%i' % (i + 1),
                'current': current == str(i),
                'visible': True,
                'url': url,
            })
        return ret


class BatchedResult(BrowserView):

    @property
    def batch(self):
        return ExampleBatch(self.context, self.request)()

    @property
    def slice(self):
        result = range(RESULTLEN)
        current = int(self.request.get('b_page', '0'))
        start = current * SLICESIZE
        end = start + SLICESIZE
        return result[start:end]
