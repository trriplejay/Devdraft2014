#pylint: disable=all
import sys
import bisect


class MatchMakingPool(object):

    def __init__(self, thresh):
        # set up our internals, only need a threshold to start the pool
        self.idList = []
        self.eloList = []
        self.eloThresh = thresh
        self.matches = 0
        self.eloSum = 0

    def addPlayer(self, playerID, playerElo, index):
        """
        when a new player is added, put their information in both
        the elo list and the id list.  This function assumes
        that the desired index for the player is known such that the Elo list
        maintains sorted order. This index is calculated in the newLogon method
        """

        self.idList.insert(index, playerID)
        self.eloList.insert(index, playerElo)

    def removePlayer(self, index):
        """
        Remove the player at index.  Make sure to always remove from both
        lists such that they do not become out of sync with each other.
        """

        self.eloList.pop(index)
        self.idList.pop(index)

    def newLogoff(self, playerID):
        """
        When a person logs off, first check that their ID exists.  If it does,
        use the ID to find the index of the player, and call removePlayer
        to delete them permanently.  If the ID does not exist, do nothing.
        """
        if playerID in self.idList:
            playerIndex = self.idList.index(playerID)
            self.removePlayer(playerIndex)

    def newLogon(self, playerID, playerElo):
        """
        When we receive info for a player logging on, several things can
        happen.  The player could be matched with an existing player, or the
        player could just get added to the list.  To determine if there wil be
        a match, we must examine the two closest Elo values to the player (one
        above and one below, based on the fact that the list is sorted).  Then
        we determine which player is closest in Elo, and match the new player
        with that player.  If two players have the same Elo difference with the
        new player, we choose the higher Elo player to match with by default.
        When matched, the new player is never added to the player list or
        player dict, and the matched player is removed via newLogoff command
        """
        indexToInsert = bisect.bisect(self.eloList, playerElo)

        """
        Check values surrounding the index for matches.  There should be no
        need to look beyond one index higher, and one lower, since the
        list is sorted by Elo.
        """
        lowerElo = None
        higherElo = None
        highDiff = None
        lowDiff = None

        if indexToInsert > 0:
            """
            if the player will not occupy the first slot in the list based
            on his calculated index, then there must be at least one player
            ahead that can be tested for meeting the Elo threshold
            """
            lowerElo = self.eloList[indexToInsert-1]
            lowDiff = abs(lowerElo - playerElo)
            if lowDiff > int(self.eloThresh):
                #difference is too high, this player won't match
                lowDiff = None

        if indexToInsert != len(self.eloList):
            """
            if the player will not occupy the last slot in the list based
            on his calculated index, then there must be at least one player
            behind that can be tested for meeting the Elo threshold
            """
            higherElo = self.eloList[indexToInsert]
            highDiff = abs(higherElo - playerElo)
            if highDiff > int(self.eloThresh):
                #difference is too high, this player won't match
                highDiff = None

        if highDiff is not None:
            #there is a higher match within threshold
            if lowDiff is not None:
                #there is a lower match within threshold
                if highDiff <= lowDiff:
                    #there exists both a higher and lower value within
                    #threshold, and the higher value is closer
                    #to the new player's value, so match new player
                    #with higher rated player
                    self.matchPlayer(indexToInsert, highDiff)

                else:
                    #there exists both a higher and lower value within
                    #threshold, and the lower value is closer
                    #to the new player's value, so match new player
                    #with lower rated player
                    self.matchPlayer(indexToInsert, lowDiff, -1)

            else:
                #there exists a higher value within threshold, but no
                #lower value, so match new player with the higher
                #rated player
                self.matchPlayer(indexToInsert, highDiff)

        else:
            if lowDiff is not None:
                #there exists a lower value within threshold, but no
                #higher value, so match new player with the lower
                #rated player
                self.matchPlayer(indexToInsert, lowDiff, -1)

            else:
                #no existing players are within Elo threshold
                #with the new player, so just add the player to
                #the match pool
                self.addPlayer(playerID, playerElo, indexToInsert)

    def matchPlayer(self, index, eloDiff, modifier=0):
        """
        when a player in the pool is matched with a new player, they are
        immediately removed from the pool, and then the Elo sum is modified
        based on the difference (eloDiff).  The match counter is also
        incremented.  The new payer never entered the pool, and so does not
        need to be removed.
        """
        self.removePlayer(index+modifier)
        self.eloSum = self.eloSum + eloDiff
        self.matches = self.matches + 1


if __name__ == '__main__':

    """
    Matchmaking
        1. one event per line, the event to unfold as follows:
            a. read line from stdin
            b1. if "logoff", perform logoff
            b2. else check waiting pool for matching player
            c. if no matching player, add player to pool, NEXTLINE
            c. found first match
            d. quick check for second match
            e. second closer in value? if so, then match with second
            f. else match with first
            g. remove matched player from pool, add to match and Elo counts
            h. NEXTLINE
    Implementation summary:
        Use two standard python lists to hold the players.  One list contains
        Elo values, the other contains IDs.  The players are inserted into
        the list in such a way that the Elo list will always be sorted from
        low to high, and the ID list will match indecies with the Elo list.
        This allows for O(1) access time to values in the list when the index
        is known.

        Since the Elo list is sorted, the bisect function can be used
        to find the index where a new player would be inserted, and then
        use that info to check other nearby players for matches.  If no match
        is made, the list insert function will be used to add the player to the
        pool at the appropriate index to maintain a sorted Elo list.

        If a match is triggered at that insertion point, then remove the
        matched player (the new player was never actually inserted) and add
        their Elo difference to the running total.

        complexity analysis:
            reading from file:
                O(n) from iterations in readline loop
                for each iteration:
                logging on:
                    O(log n) from bisect
                    O(n) for removing player if matched
                    O(n) for inserting player if not matched
                    O(2n+logn) total
                logging off:
                    O(n) for finding id in list
                    O(n) for getting index of id in list
                    O(n) for removing id from list
                    O(3n) total
            total: O(n*(n+logn)) or O(n^2 + nlogn) or just O(n^2) for large n

            improvement: need to find a way to eliminate the O(n) insert and
                deletion time of lists.  One possible solution would be to
                create my own balanced BST implementation, to ensure logn
                insert, delete, and lookup times.  However, you would need
                two separate trees: one sorted by Elo, and one sorted by ID,
                otherwise doing a lookup by ID would still take O(n) time. This
                would increase the space complexity over the implementation of
                two integer lists.  Another possibility is to add a dict
                to allow O(1) lookup times, but one list would still be
                needed to hold sorted Elo values.  The sorted values are
                important to keep in order to avoid costly search times when
                looking for Elo scores that are within threshold of a player
                who is logging in.  Sorted list lets you focus on the two
                nearest players instead of having to search all n players
                for teh closest.

    """

    eloThresh, num_events = sys.stdin.readline().split()

    #instantiate the pool object
    myPool = MatchMakingPool(eloThresh)

    for i in range(int(num_events)):
        playerInfo = sys.stdin.readline().strip()
        splitline = playerInfo.split(" ")
        playerAction = splitline[0].lower()
        playerID = int(splitline[1])

        if(playerAction=="logon"):
            playerElo = int(splitline[2])
            #logon the player
            myPool.newLogon(playerID, playerElo)

        elif playerAction == "logoff":
            #call the logoff method which will locate
            #and eliminate the player
            myPool.newLogoff(playerID)


    #outside the loop, print the final results
    print str(myPool.matches) + " " + str(myPool.eloSum) + " " + str(len(myPool.idList))
