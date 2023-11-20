    # @func_timeout.func_set_timeout(30)
    # def receiveCanMessage(self, canID=None):
    #     try:
    #         msg = self.client.socketSub.recv()
    #         respObj = CanCmd.Das2ClientFlow()
    #         respObj.ParseFromString(msg[self.TopicLength:])
    #         if canID is None or respObj.ID == canID:
    #             return respObj
    #         else:
    #             return None
    #     except func_timeout.FunctionTimedOut:
    #         return None