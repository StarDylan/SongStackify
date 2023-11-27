# Concurrency
## Case 1 - Lost Update
Multiple instances of the same user attempts to listen to the same playlist.

This issue arrises since changes to playlist position are not idempotent.

We serialized this transaction to prevent this. Write speed is not super important as we do not expect many instances of a user to access the service.

## Case 2 - Non-repeatable Read
A user attempts to play a song via Play Playlist while another user deletes the song from the service.

This would be prevented by changing the isolation level to Repeatable Read but due to Case 1 above, the transaction is Serialiable anyways.

## Case 3 - Write Skew
A user attempts to add a link to a song that does not exist while another user also attempts to add the same link to the same song for the same platform.

The add song transaction is made serializable, we do not anticipate a large volume of writes to the links table, compared to reads, so the performance hit is acceptable.

