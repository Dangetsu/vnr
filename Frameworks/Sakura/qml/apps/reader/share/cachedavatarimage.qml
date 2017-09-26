/** cachedavatarimage.qml
 *  2/21/2013 jichi
 */
import QtQuick 1.1
//import org.sakuradite.reader 1.0 as Plugin
import '.' as Share

Share.AvatarImage {

  property int userId
  property int userHash

  // - Private -

  url: !userId ? '' : datamanPlugin_.queryUserAvatarUrlWithHash(userId, userHash)

  //Plugin.DataManagerProxy { id: dataman_ }
}
